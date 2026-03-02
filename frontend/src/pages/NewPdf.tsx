import { ChatServices } from '@/apis/services/chat.service';
import { DocumentServices } from '@/apis/services/document.service';
import { ErrorAlert } from '@/components';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { z } from 'zod';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // MB * KB * BYTES

const pdfSchema = z.object({
  file: z
    .instanceof(FileList)
    .refine((files) => files.length > 0, 'PDF file is required')
    .refine((files) => files[0]?.type === 'application/pdf', 'Only PDF files are allowed')
    .refine((files) => files[0]?.size <= MAX_FILE_SIZE, 'File size must be less than 5MB'),
});

type PdfFormData = z.infer<typeof pdfSchema>;

export default function NewPdf() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PdfFormData>({
    resolver: zodResolver(pdfSchema),
  });

  const onSubmit = async (data: PdfFormData) => {
    try {
      setLoading(true);
      setError(null);
      const res = await DocumentServices.upload(data.file[0]);
      console.log('Upload success:', res);
      // ASK EXPLICT OR FIND BETTER WAY
      const summaryQuestion =
        'Provide a detailed summary of this document in paragraph form, covering all the main points and key information.';
      const summaryResponse = await ChatServices.ask({
        document_id: res.document_id,
        question: summaryQuestion,
      });
      console.log('Auto-summary:', summaryResponse);

      navigate(`/chat/${summaryResponse.session_id}?document_id=${res.document_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to upload PDF');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100 bg-light">
      <div className="card shadow p-4" style={{ width: '400px' }}>
        <h2 className="text-center mb-4">Upload PDF</h2>
        <ErrorAlert message={error} />
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="mb-3">
            <label htmlFor="file" className="form-label">
              PDF File
            </label>
            <input
              type="file"
              id="file"
              accept="application/pdf"
              className={`form-control ${errors.file ? 'is-invalid' : ''}`}
              {...register('file')}
            />
            {errors.file && (
              <div className="invalid-feedback">{errors.file.message?.toString()}</div>
            )}
          </div>
          <button type="submit" className="btn btn-primary w-100" disabled={loading}>
            {loading ? 'Uploading...' : 'Upload'}
          </button>
        </form>
        <p className="text-center mt-3">
          <Link to="/">Back to Home</Link>
        </p>
      </div>
    </div>
  );
}
